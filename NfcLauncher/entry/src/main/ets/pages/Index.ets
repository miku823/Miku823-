import { bundleManager, common, Want } from '@kit.AbilityKit';
import { tag } from '@kit.ConnectivityKit';
import { BusinessError, deviceInfo } from '@kit.BasicServicesKit';
import { hilog } from '@kit.PerformanceAnalysisKit';
import { promptAction } from '@kit.ArkUI';
import { AppBind, BindStore, uidToHex } from '../common/BindStore';
import { parseNdefRecords } from '../common/NdefUtil';

const DOMAIN = 0x0001;
const TAG = 'NfcLauncherPage';

@Entry
@Component
struct Index {
  @State tagIdInput: string = '';
  @State bundleInput: string = '';
  @State abilityInput: string = 'EntryAbility';
  @State uriInput: string = '';
  @State autoLaunch: boolean = false;
  @State embeddedLaunch: boolean = false;
  @State binds: AppBind[] = [];
  @State lastTag: string = '-';
  @State statusMsg: string = '初始化中…';
  @State scanMode: boolean = false;
  @State writeMode: boolean = false;
  @State ndefInfo: string[] = [];
  private context: common.UIAbilityContext = getContext(this) as common.UIAbilityContext;
  private nfcRegistered: boolean = false;

  aboutToAppear(): void {
    this.binds = BindStore.load(this.context);
    this.autoLaunch = BindStore.getAutoLaunch(this.context);
  }

  // 应用退到后台再回前台时页面不重建，前台派发注册已被系统失效，
  // 必须在页面每次可见时重新注册，隐藏时注销
  onPageShow(): void {
    this.registerNfc();
  }

  onPageHide(): void {
    this.unregisterNfc();
  }

  private registerNfc(): void {
    if (this.nfcRegistered) {
      return;
    }
    if (!canIUse('SystemCapability.Communication.NFC.Tag')) {
      this.statusMsg = '当前设备不支持NFC标签读取';
      return;
    }
    try {
      let elementName: bundleManager.ElementName = {
        bundleName: this.context.abilityInfo.bundleName,
        abilityName: this.context.abilityInfo.name,
        moduleName: 'entry'
      };
      let techs: number[] = [tag.NFC_A, tag.NFC_B, tag.NFC_F, tag.NFC_V];
      tag.registerForegroundDispatch(elementName, techs, this.onTagDiscovered);
      this.nfcRegistered = true;
      this.statusMsg = 'NFC已就绪，贴近标签即可读取';
    } catch (e) {
      let err = e as BusinessError;
      hilog.error(DOMAIN, TAG, 'registerForegroundDispatch failed: %{public}d %{public}s', err.code, err.message);
      this.statusMsg = `NFC注册失败: ${err.code} ${err.message}`;
    }
  }

  private unregisterNfc(): void {
    if (!this.nfcRegistered) {
      return;
    }
    try {
      let elementName: bundleManager.ElementName = {
        bundleName: this.context.abilityInfo.bundleName,
        abilityName: this.context.abilityInfo.name,
        moduleName: 'entry'
      };
      tag.unregisterForegroundDispatch(elementName);
    } catch (e) {
      hilog.warn(DOMAIN, TAG, 'unregisterForegroundDispatch failed');
    }
    this.nfcRegistered = false;
  }

  private onTagDiscovered = (err: BusinessError, tagInfo: tag.TagInfo): void => {
    if (err) {
      this.statusMsg = `读取标签失败: ${err.message}`;
      return;
    }
    let hex = uidToHex(tagInfo.uid);
    hilog.info(DOMAIN, TAG, 'tag discovered: %{public}s', hex);
    // 写卡模式优先：把直达链接写入贴近的空白卡
    if (this.writeMode) {
      this.lastTag = hex;
      this.writeTag(tagInfo);
      return;
    }
    if (this.scanMode) {
      this.inspectTag(hex, tagInfo);
      return;
    }
    if (this.tagIdInput.trim() === '') {
      this.tagIdInput = hex;
    }
    this.handleTag(hex, false);
  };

  private inspectTag(hex: string, tagInfo: tag.TagInfo): void {
    this.lastTag = hex;
    let lines: string[] = [`UID: ${hex}`, `技术类型: ${tagInfo.technology.join(', ')}`];
    try {
      let ndefTag = tag.getNdef(tagInfo);
      if (!ndefTag) {
        lines.push('该标签不支持 NDEF');
      } else {
        let msg = ndefTag.getNdefMessage();
        if (!msg || msg.getNdefRecords().length === 0) {
          lines.push('NDEF 消息为空（标签未写入内容）');
        } else {
          let infos = parseNdefRecords(msg.getNdefRecords());
          for (let info of infos) {
            lines.push(`${info.type}: ${info.content}`);
          }
          // 识别到的 URI / 应用包名自动回填到输入框
          let uriInfo = infos.find(i => i.type === 'URI');
          if (uriInfo) {
            this.uriInput = uriInfo.content;
          }
          let aarInfo = infos.find(i => i.type === 'AAR');
          if (aarInfo) {
            this.bundleInput = aarInfo.content;
          }
        }
      }
    } catch (e) {
      let err = e as BusinessError;
      lines.push(`读取NDEF失败: ${err.code} ${err.message}`);
    }
    this.ndefInfo = lines;
    this.statusMsg = '识别完成（识别模式不触发跳转）';
  }

  private toast(message: string): void {
    // openToast 需要 API 18+，低版本设备静默降级
    if (deviceInfo.sdkApiVersion >= 18) {
      try {
        promptAction.openToast({ message: message });
      } catch (e) {
        // ignore toast failure
      }
    }
  }

  private handleTag(hex: string, forceLaunch: boolean): void {
    this.lastTag = hex;
    let hit = this.binds.find(b => b.tagId.toUpperCase() === hex);
    if (hit && (this.autoLaunch || forceLaunch)) {
      this.statusMsg = `${forceLaunch ? '模拟触发' : '识别到'}标签 ${hex}，正在跳转…`;
      this.launchApp(hit.bundleName, hit.abilityName, hit.uri);
    } else if (hit) {
      this.statusMsg = `识别到已绑定标签: ${hex}（自动跳转未开启）`;
    } else {
      this.statusMsg = `未绑定的标签: ${hex}，请先保存绑定`;
    }
  }

  private launchApp(bundleName: string, abilityName: string, uri: string): void {
    let want: Want;
    if (uri !== '') {
      want = {
        action: 'ohos.want.action.viewData',
        uri: uri
      };
    } else {
      want = {
        bundleName: bundleName,
        abilityName: abilityName
      };
    }
    // embedded 模式：目标应用嵌入到本应用窗口，绕过应用切换拦截
    if (this.embeddedLaunch) {
      want.parameters = {
        'windowMode': 2  // WINDOW_MODE_EMBEDDED
      };
    }
    let mode = this.embeddedLaunch ? 'embedded嵌入' : '普通';
    this.context.startAbility(want)
      .then(() => {
        if (uri !== '') {
          this.statusMsg = `已通过链接${mode}拉起目标页面`;
        } else {
          this.statusMsg = `已${mode}拉起 ${bundleName}`;
        }
      })
      .catch((err: BusinessError) => {
        hilog.error(DOMAIN, TAG, 'startAbility failed: %{public}d %{public}s', err.code, err.message);
        this.statusMsg = `跳转失败(${mode}): ${err.code} ${err.message}`;
        this.toast(`跳转失败: ${err.message}`);
      });
  }

  private saveBind(): void {
    let tagId = this.tagIdInput.trim().toUpperCase();
    let bundle = this.bundleInput.trim();
    let ability = this.abilityInput.trim();
    let uri = this.uriInput.trim();
    if (tagId === '' || (bundle === '' && uri === '')) {
      this.toast('请填写NFC标签ID，以及包名或直达链接');
      return;
    }
    if (ability === '') {
      ability = 'EntryAbility';
    }
    let bind: AppBind = { tagId: tagId, bundleName: bundle, abilityName: ability, uri: uri };
    BindStore.save(this.context, bind);
    this.binds = BindStore.load(this.context);
    this.statusMsg = `已保存绑定: ${tagId} → ${bundle}`;
  }

  private simulateTag(): void {
    let hex = (this.tagIdInput.trim() !== '' ? this.tagIdInput : this.lastTag).trim().toUpperCase();
    if (hex === '' || hex === '-') {
      this.toast('请先输入或读取NFC标签ID');
      return;
    }
    hilog.info(DOMAIN, TAG, 'simulate tag: %{public}s', hex);
    this.handleTag(hex, true);
  }

  // 把「直达链接」框中的内容作为 NDEF URI 记录写入贴近的卡片
  private writeTag(tagInfo: tag.TagInfo): void {
    this.writeMode = false; // 一次性写入，避免卡片停留时反复触发
    let uri = this.uriInput.trim();
    if (uri === '') {
      this.statusMsg = '写卡失败：请先在直达链接框填写要写入的链接';
      return;
    }
    try {
      let ndefTag = tag.getNdef(tagInfo);
      if (!ndefTag) {
        this.statusMsg = '写卡失败：该卡不支持 NDEF（请用 NTAG213/215 等空白卡）';
        return;
      }
      if (!ndefTag.isNdefWritable()) {
        this.statusMsg = '写卡失败：卡片不可写（已锁定或不支持写入）';
        return;
      }
      // 系统工厂自动处理 URI 前缀压缩
      let record = tag.ndef.makeUriRecord(uri);
      let msg = tag.ndef.createNdefMessage([record]);
      if (!ndefTag.isTagConnected()) {
        ndefTag.connect();
      }
      ndefTag.writeNdef(msg)
        .then(() => {
          this.statusMsg = '写卡成功，现在贴这张卡即可触发跳转';
          this.toast('写卡成功');
        })
        .catch((err: BusinessError) => {
          hilog.error(DOMAIN, TAG, 'writeNdef failed: %{public}d %{public}s', err.code, err.message);
          this.statusMsg = `写卡失败: ${err.code} ${err.message}`;
        });
    } catch (e) {
      let err = e as BusinessError;
      hilog.error(DOMAIN, TAG, 'writeTag failed: %{public}d %{public}s', err.code, err.message);
      this.statusMsg = `写卡失败: ${err.code} ${err.message}`;
    }
  }

  build() {
    Column({ space: 12 }) {
      Text('NFC跳转助手')
        .fontSize(26)
        .fontWeight(FontWeight.Bold)
        .margin({ top: 16 })

      Text(this.statusMsg)
        .fontSize(13)
        .fontColor('#666666')
        .width('100%')

      Row({ space: 12 }) {
        Button('绑定模式')
          .layoutWeight(1)
          .backgroundColor(this.scanMode ? '#F2F3F5' : '#007DFF')
          .fontColor(this.scanMode ? '#333333' : '#FFFFFF')
          .onClick(() => {
            this.scanMode = false;
            this.statusMsg = '绑定模式：贴近标签触发跳转';
          })
        Button('识别模式')
          .layoutWeight(1)
          .backgroundColor(this.scanMode ? '#007DFF' : '#F2F3F5')
          .fontColor(this.scanMode ? '#FFFFFF' : '#333333')
          .onClick(() => {
            this.scanMode = true;
            this.statusMsg = '识别模式：贴近标签读取内容';
          })
      }
      .width('100%')

      TextInput({ placeholder: 'NFC标签ID（贴近标签可自动填充）', text: this.tagIdInput })
        .height(48)
        .onChange((v: string) => {
          this.tagIdInput = v;
        })

      TextInput({ placeholder: '应用包名，如 com.huawei.hmos.settings', text: this.bundleInput })
        .height(48)
        .onChange((v: string) => {
          this.bundleInput = v;
        })

      TextInput({ placeholder: 'Ability名称（默认 EntryAbility）', text: this.abilityInput })
        .height(48)
        .onChange((v: string) => {
          this.abilityInput = v;
        })

      TextInput({ placeholder: '直达链接（可选），如 alipays://platformapi/startapp?appId=小程序ID', text: this.uriInput })
        .height(48)
        .onChange((v: string) => {
          this.uriInput = v;
        })

      Button('保存绑定')
        .width('100%')
        .onClick(() => {
          this.saveBind();
        })

      Button('模拟NFC触发（按输入的标签ID跳转）')
        .width('100%')
        .backgroundColor('#007DFF')
        .onClick(() => {
          this.simulateTag();
        })

      Button(this.writeMode ? '取消写卡' : '写入空白卡（将直达链接写入下一张贴近的卡）')
        .width('100%')
        .backgroundColor(this.writeMode ? '#E84026' : '#00AA55')
        .onClick(() => {
          if (!this.writeMode && this.uriInput.trim() === '') {
            this.toast('请先在直达链接框填写要写入的链接');
            return;
          }
          this.writeMode = !this.writeMode;
          this.statusMsg = this.writeMode ? '写卡模式：请贴近空白NFC卡…' : '已取消写卡';
        })

      Row() {
        Text('贴近已绑定标签时自动跳转')
          .fontSize(15)
          .layoutWeight(1)
        Toggle({ type: ToggleType.Switch, isOn: this.autoLaunch })
          .onChange((on: boolean) => {
            this.autoLaunch = on;
            BindStore.setAutoLaunch(this.context, on);
          })
      }
      .width('100%')

      Row() {
        Text('Embedded嵌入模式（绕过应用切换拦截）')
          .fontSize(15)
          .layoutWeight(1)
        Toggle({ type: ToggleType.Switch, isOn: this.embeddedLaunch })
          .onChange((on: boolean) => {
            this.embeddedLaunch = on;
            this.statusMsg = on ? '已开启Embedded嵌入模式' : '已切换回普通跳转模式';
          })
      }
      .width('100%')

      Text(`最近读取的标签: ${this.lastTag}`)
        .fontSize(13)
        .fontColor('#888888')
        .width('100%')

      if (this.scanMode && this.ndefInfo.length > 0) {
        Column({ space: 4 }) {
          Text('识别结果')
            .fontSize(15)
            .fontWeight(FontWeight.Medium)
          ForEach(this.ndefInfo, (line: string) => {
            Text(line)
              .fontSize(13)
              .fontColor('#333333')
              .width('100%')
          }, (line: string) => line)
        }
        .width('100%')
        .padding(10)
        .backgroundColor('#FFF7E6')
        .borderRadius(10)
        .alignItems(HorizontalAlign.Start)
      }

      Text('已绑定列表')
        .fontSize(17)
        .fontWeight(FontWeight.Medium)
        .width('100%')
        .margin({ top: 8 })

      List({ space: 8 }) {
        ForEach(this.binds, (item: AppBind) => {
          ListItem() {
            Row() {
              Column({ space: 2 }) {
                Text(item.tagId)
                  .fontSize(14)
                  .fontWeight(FontWeight.Medium)
                Text(item.uri !== '' ? `直达: ${item.uri}` : `${item.bundleName} / ${item.abilityName}`)
                  .fontSize(12)
                  .fontColor('#888888')
                  .maxLines(1)
                  .textOverflow({ overflow: TextOverflow.Ellipsis })
              }
              .alignItems(HorizontalAlign.Start)
              .layoutWeight(1)

              Button('删除')
                .fontSize(12)
                .height(30)
                .backgroundColor('#F2F3F5')
                .fontColor('#E84026')
                .onClick(() => {
                  BindStore.remove(this.context, item.tagId);
                  this.binds = BindStore.load(this.context);
                  this.statusMsg = `已删除绑定: ${item.tagId}`;
                })
            }
            .width('100%')
            .padding(10)
            .backgroundColor('#F7F8FA')
            .borderRadius(10)
            .onClick(() => {
              this.tagIdInput = item.tagId;
              this.bundleInput = item.bundleName;
              this.abilityInput = item.abilityName;
              this.uriInput = item.uri;
              this.statusMsg = `已回填配置: ${item.tagId}`;
            })
          }
        }, (item: AppBind) => item.tagId)
      }
      .layoutWeight(1)
      .width('100%')
    }
    .width('100%')
    .height('100%')
    .padding({ left: 20, right: 20, bottom: 20 })
  }
}

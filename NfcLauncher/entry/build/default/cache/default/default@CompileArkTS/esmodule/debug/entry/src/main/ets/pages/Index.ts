if (!("finalizeConstruction" in ViewPU.prototype)) {
    Reflect.set(ViewPU.prototype, "finalizeConstruction", () => { });
}
interface Index_Params {
    tagIdInput?: string;
    bundleInput?: string;
    abilityInput?: string;
    uriInput?: string;
    autoLaunch?: boolean;
    embeddedLaunch?: boolean;
    binds?: AppBind[];
    lastTag?: string;
    statusMsg?: string;
    scanMode?: boolean;
    writeMode?: boolean;
    ndefInfo?: string[];
    context?: common.UIAbilityContext;
    nfcRegistered?: boolean;
    onTagDiscovered?;
}
import type bundleManager from "@ohos:bundle.bundleManager";
import type common from "@ohos:app.ability.common";
import type Want from "@ohos:app.ability.Want";
import tag from "@ohos:nfc.tag";
import type { BusinessError } from "@ohos:base";
import deviceInfo from "@ohos:deviceInfo";
import hilog from "@ohos:hilog";
import promptAction from "@ohos:promptAction";
import { BindStore, uidToHex } from "@bundle:com.example.nfclauncher/entry/ets/common/BindStore";
import type { AppBind } from "@bundle:com.example.nfclauncher/entry/ets/common/BindStore";
import { parseNdefRecords } from "@bundle:com.example.nfclauncher/entry/ets/common/NdefUtil";
const DOMAIN = 0x0001;
const TAG = 'NfcLauncherPage';
class Index extends ViewPU {
    constructor(parent, params, __localStorage, elmtId = -1, paramsLambda = undefined, extraInfo) {
        super(parent, __localStorage, elmtId, extraInfo);
        if (typeof paramsLambda === "function") {
            this.paramsGenerator_ = paramsLambda;
        }
        this.__tagIdInput = new ObservedPropertySimplePU('', this, "tagIdInput");
        this.__bundleInput = new ObservedPropertySimplePU('', this, "bundleInput");
        this.__abilityInput = new ObservedPropertySimplePU('EntryAbility', this, "abilityInput");
        this.__uriInput = new ObservedPropertySimplePU('', this, "uriInput");
        this.__autoLaunch = new ObservedPropertySimplePU(false, this, "autoLaunch");
        this.__embeddedLaunch = new ObservedPropertySimplePU(false, this, "embeddedLaunch");
        this.__binds = new ObservedPropertyObjectPU([], this, "binds");
        this.__lastTag = new ObservedPropertySimplePU('-', this, "lastTag");
        this.__statusMsg = new ObservedPropertySimplePU('初始化中…', this, "statusMsg");
        this.__scanMode = new ObservedPropertySimplePU(false, this, "scanMode");
        this.__writeMode = new ObservedPropertySimplePU(false, this, "writeMode");
        this.__ndefInfo = new ObservedPropertyObjectPU([], this, "ndefInfo");
        this.context = getContext(this) as common.UIAbilityContext;
        this.nfcRegistered = false;
        this.onTagDiscovered = (err: BusinessError, tagInfo: tag.TagInfo): void => {
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
        this.setInitiallyProvidedValue(params);
        this.finalizeConstruction();
    }
    setInitiallyProvidedValue(params: Index_Params) {
        if (params.tagIdInput !== undefined) {
            this.tagIdInput = params.tagIdInput;
        }
        if (params.bundleInput !== undefined) {
            this.bundleInput = params.bundleInput;
        }
        if (params.abilityInput !== undefined) {
            this.abilityInput = params.abilityInput;
        }
        if (params.uriInput !== undefined) {
            this.uriInput = params.uriInput;
        }
        if (params.autoLaunch !== undefined) {
            this.autoLaunch = params.autoLaunch;
        }
        if (params.embeddedLaunch !== undefined) {
            this.embeddedLaunch = params.embeddedLaunch;
        }
        if (params.binds !== undefined) {
            this.binds = params.binds;
        }
        if (params.lastTag !== undefined) {
            this.lastTag = params.lastTag;
        }
        if (params.statusMsg !== undefined) {
            this.statusMsg = params.statusMsg;
        }
        if (params.scanMode !== undefined) {
            this.scanMode = params.scanMode;
        }
        if (params.writeMode !== undefined) {
            this.writeMode = params.writeMode;
        }
        if (params.ndefInfo !== undefined) {
            this.ndefInfo = params.ndefInfo;
        }
        if (params.context !== undefined) {
            this.context = params.context;
        }
        if (params.nfcRegistered !== undefined) {
            this.nfcRegistered = params.nfcRegistered;
        }
        if (params.onTagDiscovered !== undefined) {
            this.onTagDiscovered = params.onTagDiscovered;
        }
    }
    updateStateVars(params: Index_Params) {
    }
    purgeVariableDependenciesOnElmtId(rmElmtId) {
        this.__tagIdInput.purgeDependencyOnElmtId(rmElmtId);
        this.__bundleInput.purgeDependencyOnElmtId(rmElmtId);
        this.__abilityInput.purgeDependencyOnElmtId(rmElmtId);
        this.__uriInput.purgeDependencyOnElmtId(rmElmtId);
        this.__autoLaunch.purgeDependencyOnElmtId(rmElmtId);
        this.__embeddedLaunch.purgeDependencyOnElmtId(rmElmtId);
        this.__binds.purgeDependencyOnElmtId(rmElmtId);
        this.__lastTag.purgeDependencyOnElmtId(rmElmtId);
        this.__statusMsg.purgeDependencyOnElmtId(rmElmtId);
        this.__scanMode.purgeDependencyOnElmtId(rmElmtId);
        this.__writeMode.purgeDependencyOnElmtId(rmElmtId);
        this.__ndefInfo.purgeDependencyOnElmtId(rmElmtId);
    }
    aboutToBeDeleted() {
        this.__tagIdInput.aboutToBeDeleted();
        this.__bundleInput.aboutToBeDeleted();
        this.__abilityInput.aboutToBeDeleted();
        this.__uriInput.aboutToBeDeleted();
        this.__autoLaunch.aboutToBeDeleted();
        this.__embeddedLaunch.aboutToBeDeleted();
        this.__binds.aboutToBeDeleted();
        this.__lastTag.aboutToBeDeleted();
        this.__statusMsg.aboutToBeDeleted();
        this.__scanMode.aboutToBeDeleted();
        this.__writeMode.aboutToBeDeleted();
        this.__ndefInfo.aboutToBeDeleted();
        SubscriberManager.Get().delete(this.id__());
        this.aboutToBeDeletedInternal();
    }
    private __tagIdInput: ObservedPropertySimplePU<string>;
    get tagIdInput() {
        return this.__tagIdInput.get();
    }
    set tagIdInput(newValue: string) {
        this.__tagIdInput.set(newValue);
    }
    private __bundleInput: ObservedPropertySimplePU<string>;
    get bundleInput() {
        return this.__bundleInput.get();
    }
    set bundleInput(newValue: string) {
        this.__bundleInput.set(newValue);
    }
    private __abilityInput: ObservedPropertySimplePU<string>;
    get abilityInput() {
        return this.__abilityInput.get();
    }
    set abilityInput(newValue: string) {
        this.__abilityInput.set(newValue);
    }
    private __uriInput: ObservedPropertySimplePU<string>;
    get uriInput() {
        return this.__uriInput.get();
    }
    set uriInput(newValue: string) {
        this.__uriInput.set(newValue);
    }
    private __autoLaunch: ObservedPropertySimplePU<boolean>;
    get autoLaunch() {
        return this.__autoLaunch.get();
    }
    set autoLaunch(newValue: boolean) {
        this.__autoLaunch.set(newValue);
    }
    private __embeddedLaunch: ObservedPropertySimplePU<boolean>;
    get embeddedLaunch() {
        return this.__embeddedLaunch.get();
    }
    set embeddedLaunch(newValue: boolean) {
        this.__embeddedLaunch.set(newValue);
    }
    private __binds: ObservedPropertyObjectPU<AppBind[]>;
    get binds() {
        return this.__binds.get();
    }
    set binds(newValue: AppBind[]) {
        this.__binds.set(newValue);
    }
    private __lastTag: ObservedPropertySimplePU<string>;
    get lastTag() {
        return this.__lastTag.get();
    }
    set lastTag(newValue: string) {
        this.__lastTag.set(newValue);
    }
    private __statusMsg: ObservedPropertySimplePU<string>;
    get statusMsg() {
        return this.__statusMsg.get();
    }
    set statusMsg(newValue: string) {
        this.__statusMsg.set(newValue);
    }
    private __scanMode: ObservedPropertySimplePU<boolean>;
    get scanMode() {
        return this.__scanMode.get();
    }
    set scanMode(newValue: boolean) {
        this.__scanMode.set(newValue);
    }
    private __writeMode: ObservedPropertySimplePU<boolean>;
    get writeMode() {
        return this.__writeMode.get();
    }
    set writeMode(newValue: boolean) {
        this.__writeMode.set(newValue);
    }
    private __ndefInfo: ObservedPropertyObjectPU<string[]>;
    get ndefInfo() {
        return this.__ndefInfo.get();
    }
    set ndefInfo(newValue: string[]) {
        this.__ndefInfo.set(newValue);
    }
    private context: common.UIAbilityContext;
    private nfcRegistered: boolean;
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
        }
        catch (e) {
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
        }
        catch (e) {
            hilog.warn(DOMAIN, TAG, 'unregisterForegroundDispatch failed');
        }
        this.nfcRegistered = false;
    }
    private onTagDiscovered;
    private inspectTag(hex: string, tagInfo: tag.TagInfo): void {
        this.lastTag = hex;
        let lines: string[] = [`UID: ${hex}`, `技术类型: ${tagInfo.technology.join(', ')}`];
        try {
            let ndefTag = tag.getNdef(tagInfo);
            if (!ndefTag) {
                lines.push('该标签不支持 NDEF');
            }
            else {
                let msg = ndefTag.getNdefMessage();
                if (!msg || msg.getNdefRecords().length === 0) {
                    lines.push('NDEF 消息为空（标签未写入内容）');
                }
                else {
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
        }
        catch (e) {
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
            }
            catch (e) {
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
        }
        else if (hit) {
            this.statusMsg = `识别到已绑定标签: ${hex}（自动跳转未开启）`;
        }
        else {
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
        }
        else {
            want = {
                bundleName: bundleName,
                abilityName: abilityName
            };
        }
        // embedded 模式：目标应用嵌入到本应用窗口，绕过应用切换拦截
        if (this.embeddedLaunch) {
            want.parameters = {
                'windowMode': 2 // WINDOW_MODE_EMBEDDED
            };
        }
        let mode = this.embeddedLaunch ? 'embedded嵌入' : '普通';
        this.context.startAbility(want)
            .then(() => {
            if (uri !== '') {
                this.statusMsg = `已通过链接${mode}拉起目标页面`;
            }
            else {
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
        }
        catch (e) {
            let err = e as BusinessError;
            hilog.error(DOMAIN, TAG, 'writeTag failed: %{public}d %{public}s', err.code, err.message);
            this.statusMsg = `写卡失败: ${err.code} ${err.message}`;
        }
    }
    initialRender() {
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Column.create({ space: 12 });
            Column.width('100%');
            Column.height('100%');
            Column.padding({ left: 20, right: 20, bottom: 20 });
        }, Column);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create('NFC跳转助手');
            Text.fontSize(26);
            Text.fontWeight(FontWeight.Bold);
            Text.margin({ top: 16 });
        }, Text);
        Text.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create(this.statusMsg);
            Text.fontSize(13);
            Text.fontColor('#666666');
            Text.width('100%');
        }, Text);
        Text.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Row.create({ space: 12 });
            Row.width('100%');
        }, Row);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Button.createWithLabel('绑定模式');
            Button.layoutWeight(1);
            Button.backgroundColor(this.scanMode ? '#F2F3F5' : '#007DFF');
            Button.fontColor(this.scanMode ? '#333333' : '#FFFFFF');
            Button.onClick(() => {
                this.scanMode = false;
                this.statusMsg = '绑定模式：贴近标签触发跳转';
            });
        }, Button);
        Button.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Button.createWithLabel('识别模式');
            Button.layoutWeight(1);
            Button.backgroundColor(this.scanMode ? '#007DFF' : '#F2F3F5');
            Button.fontColor(this.scanMode ? '#FFFFFF' : '#333333');
            Button.onClick(() => {
                this.scanMode = true;
                this.statusMsg = '识别模式：贴近标签读取内容';
            });
        }, Button);
        Button.pop();
        Row.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            TextInput.create({ placeholder: 'NFC标签ID（贴近标签可自动填充）', text: this.tagIdInput });
            TextInput.height(48);
            TextInput.onChange((v: string) => {
                this.tagIdInput = v;
            });
        }, TextInput);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            TextInput.create({ placeholder: '应用包名，如 com.huawei.hmos.settings', text: this.bundleInput });
            TextInput.height(48);
            TextInput.onChange((v: string) => {
                this.bundleInput = v;
            });
        }, TextInput);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            TextInput.create({ placeholder: 'Ability名称（默认 EntryAbility）', text: this.abilityInput });
            TextInput.height(48);
            TextInput.onChange((v: string) => {
                this.abilityInput = v;
            });
        }, TextInput);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            TextInput.create({ placeholder: '直达链接（可选），如 alipays://platformapi/startapp?appId=小程序ID', text: this.uriInput });
            TextInput.height(48);
            TextInput.onChange((v: string) => {
                this.uriInput = v;
            });
        }, TextInput);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Button.createWithLabel('保存绑定');
            Button.width('100%');
            Button.onClick(() => {
                this.saveBind();
            });
        }, Button);
        Button.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Button.createWithLabel('模拟NFC触发（按输入的标签ID跳转）');
            Button.width('100%');
            Button.backgroundColor('#007DFF');
            Button.onClick(() => {
                this.simulateTag();
            });
        }, Button);
        Button.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Button.createWithLabel(this.writeMode ? '取消写卡' : '写入空白卡（将直达链接写入下一张贴近的卡）');
            Button.width('100%');
            Button.backgroundColor(this.writeMode ? '#E84026' : '#00AA55');
            Button.onClick(() => {
                if (!this.writeMode && this.uriInput.trim() === '') {
                    this.toast('请先在直达链接框填写要写入的链接');
                    return;
                }
                this.writeMode = !this.writeMode;
                this.statusMsg = this.writeMode ? '写卡模式：请贴近空白NFC卡…' : '已取消写卡';
            });
        }, Button);
        Button.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Row.create();
            Row.width('100%');
        }, Row);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create('贴近已绑定标签时自动跳转');
            Text.fontSize(15);
            Text.layoutWeight(1);
        }, Text);
        Text.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Toggle.create({ type: ToggleType.Switch, isOn: this.autoLaunch });
            Toggle.onChange((on: boolean) => {
                this.autoLaunch = on;
                BindStore.setAutoLaunch(this.context, on);
            });
        }, Toggle);
        Toggle.pop();
        Row.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Row.create();
            Row.width('100%');
        }, Row);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create('Embedded嵌入模式（绕过应用切换拦截）');
            Text.fontSize(15);
            Text.layoutWeight(1);
        }, Text);
        Text.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Toggle.create({ type: ToggleType.Switch, isOn: this.embeddedLaunch });
            Toggle.onChange((on: boolean) => {
                this.embeddedLaunch = on;
                this.statusMsg = on ? '已开启Embedded嵌入模式' : '已切换回普通跳转模式';
            });
        }, Toggle);
        Toggle.pop();
        Row.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create(`最近读取的标签: ${this.lastTag}`);
            Text.fontSize(13);
            Text.fontColor('#888888');
            Text.width('100%');
        }, Text);
        Text.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            If.create();
            if (this.scanMode && this.ndefInfo.length > 0) {
                this.ifElseBranchUpdateFunction(0, () => {
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Column.create({ space: 4 });
                        Column.width('100%');
                        Column.padding(10);
                        Column.backgroundColor('#FFF7E6');
                        Column.borderRadius(10);
                        Column.alignItems(HorizontalAlign.Start);
                    }, Column);
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        Text.create('识别结果');
                        Text.fontSize(15);
                        Text.fontWeight(FontWeight.Medium);
                    }, Text);
                    Text.pop();
                    this.observeComponentCreation2((elmtId, isInitialRender) => {
                        ForEach.create();
                        const forEachItemGenFunction = _item => {
                            const line = _item;
                            this.observeComponentCreation2((elmtId, isInitialRender) => {
                                Text.create(line);
                                Text.fontSize(13);
                                Text.fontColor('#333333');
                                Text.width('100%');
                            }, Text);
                            Text.pop();
                        };
                        this.forEachUpdateFunction(elmtId, this.ndefInfo, forEachItemGenFunction, (line: string) => line, false, false);
                    }, ForEach);
                    ForEach.pop();
                    Column.pop();
                });
            }
            else {
                this.ifElseBranchUpdateFunction(1, () => {
                });
            }
        }, If);
        If.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            Text.create('已绑定列表');
            Text.fontSize(17);
            Text.fontWeight(FontWeight.Medium);
            Text.width('100%');
            Text.margin({ top: 8 });
        }, Text);
        Text.pop();
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            List.create({ space: 8 });
            List.layoutWeight(1);
            List.width('100%');
        }, List);
        this.observeComponentCreation2((elmtId, isInitialRender) => {
            ForEach.create();
            const forEachItemGenFunction = _item => {
                const item = _item;
                {
                    const itemCreation = (elmtId, isInitialRender) => {
                        ViewStackProcessor.StartGetAccessRecordingFor(elmtId);
                        ListItem.create(deepRenderFunction, true);
                        if (!isInitialRender) {
                            ListItem.pop();
                        }
                        ViewStackProcessor.StopGetAccessRecording();
                    };
                    const itemCreation2 = (elmtId, isInitialRender) => {
                        ListItem.create(deepRenderFunction, true);
                    };
                    const deepRenderFunction = (elmtId, isInitialRender) => {
                        itemCreation(elmtId, isInitialRender);
                        this.observeComponentCreation2((elmtId, isInitialRender) => {
                            Row.create();
                            Row.width('100%');
                            Row.padding(10);
                            Row.backgroundColor('#F7F8FA');
                            Row.borderRadius(10);
                            Row.onClick(() => {
                                this.tagIdInput = item.tagId;
                                this.bundleInput = item.bundleName;
                                this.abilityInput = item.abilityName;
                                this.uriInput = item.uri;
                                this.statusMsg = `已回填配置: ${item.tagId}`;
                            });
                        }, Row);
                        this.observeComponentCreation2((elmtId, isInitialRender) => {
                            Column.create({ space: 2 });
                            Column.alignItems(HorizontalAlign.Start);
                            Column.layoutWeight(1);
                        }, Column);
                        this.observeComponentCreation2((elmtId, isInitialRender) => {
                            Text.create(item.tagId);
                            Text.fontSize(14);
                            Text.fontWeight(FontWeight.Medium);
                        }, Text);
                        Text.pop();
                        this.observeComponentCreation2((elmtId, isInitialRender) => {
                            Text.create(item.uri !== '' ? `直达: ${item.uri}` : `${item.bundleName} / ${item.abilityName}`);
                            Text.fontSize(12);
                            Text.fontColor('#888888');
                            Text.maxLines(1);
                            Text.textOverflow({ overflow: TextOverflow.Ellipsis });
                        }, Text);
                        Text.pop();
                        Column.pop();
                        this.observeComponentCreation2((elmtId, isInitialRender) => {
                            Button.createWithLabel('删除');
                            Button.fontSize(12);
                            Button.height(30);
                            Button.backgroundColor('#F2F3F5');
                            Button.fontColor('#E84026');
                            Button.onClick(() => {
                                BindStore.remove(this.context, item.tagId);
                                this.binds = BindStore.load(this.context);
                                this.statusMsg = `已删除绑定: ${item.tagId}`;
                            });
                        }, Button);
                        Button.pop();
                        Row.pop();
                        ListItem.pop();
                    };
                    this.observeComponentCreation2(itemCreation2, ListItem);
                    ListItem.pop();
                }
            };
            this.forEachUpdateFunction(elmtId, this.binds, forEachItemGenFunction, (item: AppBind) => item.tagId, false, false);
        }, ForEach);
        ForEach.pop();
        List.pop();
        Column.pop();
    }
    rerender() {
        this.updateDirtyElements();
    }
    public __resetStateVarsOnReuse__Internal(params: Object): void {
    }
    static getEntryName(): string {
        return "Index";
    }
}
registerNamedRoute(() => new Index(undefined, {}), "", { bundleName: "com.example.nfclauncher", moduleName: "entry", pagePath: "pages/Index", pageFullPath: "entry/src/main/ets/pages/Index", integratedHsp: "false", moduleType: "followWithHap" });

import type AbilityConstant from "@ohos:app.ability.AbilityConstant";
import UIAbility from "@ohos:app.ability.UIAbility";
import type Want from "@ohos:app.ability.Want";
import hilog from "@ohos:hilog";
import type window from "@ohos:window";
const DOMAIN = 0x0001;
const TAG = 'NfcLauncher';
export default class EntryAbility extends UIAbility {
    onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {
        hilog.info(DOMAIN, TAG, 'EntryAbility onCreate');
    }
    onDestroy(): void {
        hilog.info(DOMAIN, TAG, 'EntryAbility onDestroy');
    }
    onWindowStageCreate(windowStage: window.WindowStage): void {
        windowStage.loadContent('pages/Index', (err) => {
            if (err.code) {
                hilog.error(DOMAIN, TAG, 'loadContent failed: %{public}s', JSON.stringify(err));
                return;
            }
            hilog.info(DOMAIN, TAG, 'loadContent succeeded');
        });
    }
    onWindowStageDestroy(): void {
        hilog.info(DOMAIN, TAG, 'onWindowStageDestroy');
    }
    onForeground(): void {
        hilog.info(DOMAIN, TAG, 'onForeground');
    }
    onBackground(): void {
        hilog.info(DOMAIN, TAG, 'onBackground');
    }
}

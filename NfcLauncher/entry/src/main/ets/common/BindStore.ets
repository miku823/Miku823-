import { preferences } from '@kit.ArkData';
import { common } from '@kit.AbilityKit';

export interface AppBind {
  tagId: string;
  bundleName: string;
  abilityName: string;
  uri: string;
}

const STORE_NAME = 'nfc_bind_store';
const KEY_AUTO_LAUNCH = 'auto_launch';

export class BindStore {
  private static getStore(context: common.UIAbilityContext): preferences.Preferences | null {
    try {
      return preferences.getPreferencesSync(context, { name: STORE_NAME });
    } catch (e) {
      return null;
    }
  }

  static load(context: common.UIAbilityContext): AppBind[] {
    let list: AppBind[] = [];
    let store = BindStore.getStore(context);
    if (!store) {
      return list;
    }
    try {
      let all = store.getAllSync() as Record<string, string>;
      for (let key of Object.keys(all)) {
        if (key === KEY_AUTO_LAUNCH) {
          continue;
        }
        try {
          let item = JSON.parse(all[key]) as AppBind;
          if (item.tagId) {
            list.push({
              tagId: item.tagId,
              bundleName: item.bundleName ? item.bundleName : '',
              abilityName: item.abilityName ? item.abilityName : '',
              uri: item.uri ? item.uri : ''
            });
          }
        } catch (e) {
          // ignore corrupted entry
        }
      }
    } catch (e) {
      // getAllSync failed
    }
    return list;
  }

  static save(context: common.UIAbilityContext, bind: AppBind): void {
    let store = BindStore.getStore(context);
    if (!store) {
      return;
    }
    try {
      store.putSync(bind.tagId.toUpperCase(), JSON.stringify(bind));
      store.flush();
    } catch (e) {
      // ignore write failure
    }
  }

  static remove(context: common.UIAbilityContext, tagId: string): void {
    let store = BindStore.getStore(context);
    if (!store) {
      return;
    }
    try {
      store.deleteSync(tagId.toUpperCase());
      store.flush();
    } catch (e) {
      // ignore write failure
    }
  }

  static setAutoLaunch(context: common.UIAbilityContext, on: boolean): void {
    let store = BindStore.getStore(context);
    if (!store) {
      return;
    }
    try {
      store.putSync(KEY_AUTO_LAUNCH, on);
      store.flush();
    } catch (e) {
      // ignore write failure
    }
  }

  static getAutoLaunch(context: common.UIAbilityContext): boolean {
    let store = BindStore.getStore(context);
    if (!store) {
      return false;
    }
    try {
      return store.getSync(KEY_AUTO_LAUNCH, false) as boolean;
    } catch (e) {
      return false;
    }
  }
}

export function uidToHex(uid: number[]): string {
  let out = '';
  for (let b of uid) {
    let s = (b & 0xFF).toString(16).toUpperCase();
    out += s.length === 1 ? '0' + s : s;
  }
  return out;
}

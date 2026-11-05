import { tag } from '@kit.ConnectivityKit';
import { util } from '@kit.ArkTS';

export interface NdefRecordInfo {
  type: string;
  content: string;
}

// NDEF URI 记录前缀表（RTD URI）
const URI_PREFIXES: string[] = [
  '', 'http://www.', 'https://www.', 'http://', 'https://',
  'tel:', 'mailto:', 'ftp://anonymous:anonymous@', 'ftp://ftp.',
  'ftps://', 'sftp://', 'smb://', 'nfs://', 'ftp://', 'dav://',
  'news:', 'telnet://', 'imap:', 'rtsp://', 'urn:', 'pop:',
  'sip:', 'sips:', 'tftp:', 'btspp://', 'btl2cap://', 'btgoep://',
  'tcpobex://', 'irdaobex://', 'file://', 'urn:epc:id:', 'urn:epc:tag:',
  'urn:epc:pat:', 'urn:epc:raw:', 'urn:epc:', 'urn:nfc:'
];

function asciiOf(bytes: number[]): string {
  let out = '';
  for (let b of bytes) {
    out += String.fromCharCode(b & 0xFF);
  }
  return out;
}

function decodeUtf8(bytes: number[]): string {
  if (bytes.length === 0) {
    return '';
  }
  try {
    return util.TextDecoder.create('utf-8').decode(new Uint8Array(bytes), { stream: false });
  } catch (e) {
    return asciiOf(bytes);
  }
}

function hexOf(bytes: number[], max: number): string {
  let out = '';
  let n = Math.min(bytes.length, max);
  for (let i = 0; i < n; i++) {
    let s = (bytes[i] & 0xFF).toString(16).toUpperCase();
    out += (s.length === 1 ? '0' + s : s);
  }
  if (bytes.length > max) {
    out += '…';
  }
  return out;
}

export function parseNdefRecords(records: tag.NdefRecord[]): NdefRecordInfo[] {
  let out: NdefRecordInfo[] = [];
  for (let rec of records) {
    let rtd = asciiOf(rec.rtdType);
    if (rec.tnf === 1 && rtd === 'U') {
      // Well-known URI 记录：payload[0] 是前缀索引
      let prefixIdx = rec.payload.length > 0 ? rec.payload[0] : 0;
      let prefix = prefixIdx < URI_PREFIXES.length ? URI_PREFIXES[prefixIdx] : '';
      out.push({ type: 'URI', content: prefix + decodeUtf8(rec.payload.slice(1)) });
    } else if (rec.tnf === 1 && rtd === 'T') {
      // Well-known 文本记录：payload[0] 低6位是语言码长度
      let langLen = rec.payload.length > 0 ? (rec.payload[0] & 0x3F) : 0;
      out.push({ type: 'TEXT', content: decodeUtf8(rec.payload.slice(1 + langLen)) });
    } else if (rec.tnf === 4 && rtd === 'android.com:pkg') {
      // Android Application Record：payload 即应用包名
      out.push({ type: 'AAR', content: decodeUtf8(rec.payload) });
    } else if (rec.tnf === 3) {
      // Absolute URI：rtdType 本身就是完整 URI
      out.push({ type: 'URI', content: decodeUtf8(rec.rtdType) });
    } else if (rec.tnf === 2) {
      out.push({ type: `MIME(${rtd})`, content: hexOf(rec.payload, 32) });
    } else {
      out.push({ type: `RECORD(tnf=${rec.tnf}, rtd=${rtd})`, content: hexOf(rec.payload, 32) });
    }
  }
  return out;
}

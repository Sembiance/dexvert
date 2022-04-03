import {Program} from "../../Program.js";

export class darktable_rs_identify extends Program
{
	website   = "https://github.com/Sembiance/dexmagic";
	package   = "media-gfx/darktable";
	bin       = "darktable-rs-identify";
	args      = r => [r.inFile()];
	post      = r => Object.assign(r.meta, r.stdout.trim().split("\n").filter(v => !!v).map(line => (line.match(/^(?<k>[^:]+):\s+(?<v>.+)$/) || {groups : {}}).groups).reduce((result, {k, v}) => { result[k] = (v || "").replaceAll("/n", ""); return result; }, {}));
	renameOut = false;
}

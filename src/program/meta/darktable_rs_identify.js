import {Program} from "../../Program.js";

export class darktable_rs_identify extends Program
{
	website        = "https://github.com/Sembiance/dexmagic";
	gentooPackage  = "media-gfx/darktable";
	gentooUseFlags = "cups jpeg2k lua nls openexr openmp webp";

	bin  = "darktable-rs-identify";
	args = r => [r.f.input.rel];
	post = r => Object.assign(r.meta, r.stdout.trim().split("\n").filter(v => !!v).map(line => (line.match(/^(?<k>[^:]+):\s+(?<v>.+)$/) || {groups : {}}).groups).reduce((result, {k, v}) => { result[k] = (v || "").replaceAll("/n", ""); return result; }, {}));	// eslint-disable-line unicorn/prefer-object-from-entries
}

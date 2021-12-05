
import {Format} from "../../Format.js";

export class amosTracker extends Format
{
	name       = "AMOS Tracker Bank";
	website    = "https://www.exotica.org.uk/wiki/AMOS_file_formats#Regular_memory_bank_format";
	ext        = [".abk"];
	magic      = ["AMOS Memory Bank, Tracker format"];
	converters = ["amosTracker2mp3"];
	post       = dexState => Object.assign(dexState.meta, dexState.ran.find(({programid}) => programid==="amosTracker2mp3").meta);
}

import {Format} from "../../Format.js";

export class fmKingtracker extends Format
{
	name         = "FM Kingtracker";
	ext          = [".fmk"];
	magic        = ["FM Kingtracker Song", "FM-Kingtracker module"];
	metaProvider = ["musicInfo"];
	converters   = ["adplay"];
}

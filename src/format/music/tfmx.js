import {Format} from "../../Format.js";

export class tfmx extends Format
{
	name         = "The Final Musicsystem eXtended Module";
	ext          = [".mdat"];
	magic        = ["TFMX module sound data", "The Final Musicsystem eXtended module"];
	keepFilename = true;
	auxFiles     = (input, otherFiles) => (otherFiles.length>0 ? otherFiles : false);	// Requires other smpl files but hard to determine ahead of time, so just include all of it
	metaProvider = ["musicInfo"];
	converters   = ["TFMX", "TFMX-7V", "TFMX-7V-TFHD", "TFMX-Pro", "TFMX-Pro-TFHD", "TFMX-TFHD", "TFMX_ST"].map(player => `uade123[player:${player}]`);
}

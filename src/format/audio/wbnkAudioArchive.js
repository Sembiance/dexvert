import {Format} from "../../Format.js";

export class wbnkAudioArchive extends Format
{
	name       = "WBNK Audio Archive";
	ext        = [".wbnk"];
	auxFiles   = (input, otherFiles) => (otherFiles?.some(file => file.ext.toLowerCase()===".wbnk") ? otherFiles.filter(file => file.ext.toLowerCase()===".wbnk") : false);
	converters = ["unwbnk"];
}

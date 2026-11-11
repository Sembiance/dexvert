import {Format} from "../../Format.js";

export class eaPTAudio extends Format
{
	name            = "EA PT Audio";
	ext             = [".pth", ".ptd"];
	magic           = [/^vgmstream: ea_pt( |$)/];
	auxFiles        = (input, otherFiles) => otherFiles.filter(file => file.base.toLowerCase()===`${input.name.toLowerCase()}.${input.ext.toLowerCase()===".pth" ? "ptd" : "pth"}`);
	untouched       = ({f}) => f.input.ext.toLowerCase()===".ptd";
	verifyUntouched = false;
	keepFilename    = true;
	converters      = ["vgmstream[types:ea_pt]"];
}

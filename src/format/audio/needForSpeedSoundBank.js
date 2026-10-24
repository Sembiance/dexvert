import {Format} from "../../Format.js";

export class needForSpeedSoundBank extends Format
{
	name           = "The Need for Speed Sound Bank";
	ext            = [".bnk"];
	forbidExtMatch = true;
	magic          = ["The Need For Speed sounds Bank", "vgmstream: ea_eacs"];
	converters     = ["vgmstream[types:ea_eacs]"];
}

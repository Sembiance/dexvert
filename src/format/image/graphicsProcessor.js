import {Format} from "../../Format.js";

export class graphicsProcessor extends Format
{
	name       = "Graphics Processor";
	website    = "http://fileformats.archiveteam.org/wiki/Graphics_Processor";
	ext        = [".pg1", ".pg2", ".pg3"];
	converters = ["recoil2png"];
	verify     = ({meta}) => (meta.width===640 && meta.height===400) || (meta.width===320 && meta.height===200);	// with a weak extension only match, ensure it's the expected 640x400 size
}

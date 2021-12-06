import {Format} from "../../Format.js";

export class noiseTrekker extends Format
{
	name        = "NoiseTrekker Module";
	website     = "http://fileformats.archiveteam.org/wiki/Noisetrekker_module";
	ext         = [".ntk"];
	magic       = [/^NoiseTrekker v\d\.\d module$/];
	unsupported = true;
}

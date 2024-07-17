import {Format} from "../../Format.js";

export class renderManRIB extends Format
{
	name        = "RenderMan RIB";
	ext         = [".rib"];
	magic       = ["Renderman RIB"];
	unsupported = true;
	notes       = "i3dconverter claims support, but resulting .glb files are not useful";
	converters  = ["threeDObjectConverter"];
}

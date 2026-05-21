import {Format} from "../../Format.js";

export class renderManRIB extends Format
{
	name        = "RenderMan RIB";
	ext         = [".rib"];
	magic       = ["Renderman RIB"];
	converters  = ["threeDObjectConverter"];
	unsupported = true;	// only 2 unique files on discmaster. i3dconverter claims support, but resulting .glb files were not useful
}

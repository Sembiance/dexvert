import {Format} from "../../Format.js";

export class qtvrPano extends Format
{
	name       = "Quicktime VR Panoramic Image";
	magic      = ["qtvrPano"];
	converters = ["qtvr2pano"];
}

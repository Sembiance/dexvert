import {Format} from "../../Format.js";

export class glTF extends Format
{
	name         = "GL Transmission Format";
	website      = "http://fileformats.archiveteam.org/wiki/GlTF";
	ext          = [".glb", ".gltf"];
	magic        = ["GL Transmission Format", "glTF binary model", "model/gltf-binary", /^fmt\/(1315|1316)( |$)/];
	untouched    = true;
	metaProvider = ["glTFValidator", "assimpInfo"];
}

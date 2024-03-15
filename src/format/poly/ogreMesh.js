import {Format} from "../../Format.js";

export class ogreMesh extends Format
{
	name       = "OGRE Mesh";
	ext        = [".mesh.xml", ".mesh"];	// DO NOT CHANGE ORDER, needs to match longer .mesh.xml first
	magic      = ["OGRE Mesh", /^fmt\/(1188|1189)( |$)/];
	converters = dexState => (["blender[format:ogre]", "assimp", "threeDObjectConverter"].flatMap(v => (dexState.hasMagics(/^fmt\/1188( |$)/) ? ([`ogreXMLConveter129 -> ${v}`, `ogreXMLConveter120 -> ${v}`]) : v)));
}

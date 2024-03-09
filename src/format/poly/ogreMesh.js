import {Format} from "../../Format.js";

export class ogreMesh extends Format
{
	name        = "OGRE Mesh";
	ext         = [".mesh", ".mesh.xml"];
	magic       = ["OGRE Mesh", /^fmt\/(1188|1189)( |$)/];
	unsupported = true;
}

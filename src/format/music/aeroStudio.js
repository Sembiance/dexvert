import {Format} from "../../Format.js";

export class aeroStudio extends Format
{
	name        = "Aero Studio";
	ext         = [".aero"];
	magic       = ["Aero Studio song", /^fmt\/1620( |$)/];
	unsupported = true;
}

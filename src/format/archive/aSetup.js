import {Format} from "../../Format.js";

export class aSetup extends Format
{
	name        = "ASetup Installer Archive";
	ext         = [".arv"];
	magic       = ["ASetup Installer Archive"];
	unsupported = true;
	notes       = "No known extractor program.";
}

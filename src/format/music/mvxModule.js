import {Format} from "../../Format.js";

export class mvxModule extends Format
{
	name        = "MVX Module";
	ext         = [".mvm"];
	magic       = ["MVX Module"];
	unsupported = true;
}

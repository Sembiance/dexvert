import {Format} from "../../Format.js";

export class wraptor extends Format
{
	name        = "WRAptor Archive";
	ext         = [".wra", ".wr3"];
	magic       = ["WRAptor compressed", "WRAptor packer", /^fmt\/1161( |$)/];
	unsupported = true;
	notes       = "DirMaster says it supports WR3, but couldn't get anything useful from it.";
}

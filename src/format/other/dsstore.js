import {Format} from "../../Format.js";

export class dsstore extends Format
{
	name       = "Mac OS X Folder Info";
	ext        = [".ds_store"];
	magic      = ["Mac OS X folder information", "Apple Desktop Services Store", /^fmt\/394( |$)/];
	converters = ["dsstoreinfo"];
}

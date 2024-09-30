import {Format} from "../../Format.js";

export class bzip extends Format
{
	name        = "BZIP Compressed Archive";
	ext         = [".bz"];
	magic       = ["bzip compressed data", "BZIP compressed archive", "Archive: BZip1 compressed data (.BZ)", "application/x-bzip1", /^x-fmt\/267( |$)/];
	unsupported = true;
	notes       = "Was only in use for a very brief time and the only files I've encountered are the two samples that shipped with bzip-0.21";
}

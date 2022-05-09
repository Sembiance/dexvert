import {Format} from "../../Format.js";

export class authorware extends Format
{
	name        = "Authorware Application";
	ext         = [".app"];
	magic       = ["Authorware Application"];
	unsupported = true;
	notes       = "Installed the latest Authorware 7.02 (sandbox/app/) but it wouldn't open the sample files, probably because they are 'packaged'. Couldn't locate a decompilier/depackager.";
}

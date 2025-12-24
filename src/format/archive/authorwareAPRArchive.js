import {Format} from "../../Format.js";

export class authorwareAPRArchive extends Format
{
	name        = "Authorware APR Archive";
	ext         = [".apr"];
	magic       = ["Authorware APR Archive", "Authorware Archive"];
	unsupported = true;
	notes       = "Would be great to support extracting the assets out of these. Seems to be an earlier Macromedia Authorware format.";
}

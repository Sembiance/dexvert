import {Format} from "../../Format.js";

export class foxsqzArchive extends Format
{
	name       = "FOXSQZ Archive";
	ext        = [".sqz"];
	magic      = ["FOXSQZ compressed archive", "FoxSQZ archive data"];
	converters = ["foxsqz"];
}

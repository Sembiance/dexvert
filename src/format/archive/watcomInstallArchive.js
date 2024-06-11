import {Format} from "../../Format.js";

export class watcomInstallArchive extends Format
{
	name       = "WATCOM Install Archive";
	magic      = ["WATCOM Install Archive"];
	converters = ["wpack"];
}

import {Format} from "../../Format.js";

export class mTropolisArchive extends Format
{
	name       = "mTropolis Archive";
	website    = "https://en.wikipedia.org/wiki/MTropolis";
	ext        = [".mpl"];
	magic      = ["mTropolis archive"];
	converters = ["MTDisasm"];
}

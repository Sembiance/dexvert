import {Format} from "../../Format.js";

export class epocDatabase extends Format
{
	name           = "EPOC Database";
	magic          = ["Psion Series 5 database Data file", "EPOC Data database"];
	converters     = ["strings"];
}

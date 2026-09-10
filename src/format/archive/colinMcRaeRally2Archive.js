import {Format} from "../../Format.js";

export class colinMcRaeRally2Archive extends Format
{
	name       = "Colin McRae Rally 2 Archive";
	magic      = [/^geArchive: BFL_CMPR( |$)/];
	converters = ["gameextractor[codes:BFL_CMPR]"];
}

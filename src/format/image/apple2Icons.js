import {Format} from "../../Format.js";

export class apple2Icons extends Format
{
	name       = "Apple 2 Icons Archive";
	filename   = [/#CA0000$/, /#CA3F3F$/];	// eslint-disable-line unicorn/better-regex
	idMeta     = ({proDOSTypeCode}) => proDOSTypeCode==="ICN";
	converters = ["deark[module:apple2icons]", "unApple2Icons"];
}

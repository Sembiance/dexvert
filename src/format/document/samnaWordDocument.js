import {Format} from "../../Format.js";

export class samnaWordDocument extends Format
{
	name       = "Samna Word Document";
	website    = "https://winworldpc.com/product/samna-word/iii";
	ext        = [".sam", ".sm"];
	magic      = ["Samna Word document"];
	converters = ["softwareBridge[format:samna]"];
}

import {Format} from "../../Format.js";

export class ddsMIPChain extends Format
{
	name       = "DDS MIP Chain Image";
	ext        = [".dds"];
	converters = ["ddsMIPChain2png"];
}

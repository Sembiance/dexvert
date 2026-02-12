import {Format} from "../../Format.js";

export class realityBytesGameArchive extends Format
{
	name           = "Reality Bytes game archive";
	ext            = [".rbd"];
	forbidExtMatch = true;
	magic          = ["Reality Bytes game Data archive", /^geArchive: RBD( |$)/];
	converters     = ["gameextractor[codes:RBD]"];
}

import {Format} from "../../Format.js";

export class mgtFilesystem extends Format
{
	name           = "MGT Filesystem";
	website        = "https://sinclair.wiki.zxnet.co.uk/wiki/MGT_filesystem";
	ext            = [".mgt"];
	fileSize       = 819_200;	// may be other sizes, but so far only encountered this one
	converters     = ["hcdisk"];
}

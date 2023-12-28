import {Format} from "../../Format.js";

export class batchToMemory4DOS extends Format
{
	name       = "4DOS Compressed Batch-To-Memory File";
	website    = "http://fileformats.archiveteam.org/wiki/4DOS_compressed_batch_file";
	ext        = [".btm"];
	magic      = ["4DOS compressed Batch-To-Memory"];
	converters = ["fourDecomp"];
}

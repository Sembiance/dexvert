import {Format} from "../../Format.js";

export class appleQuickTakePhoto extends Format
{
	name         = "Apple QuickTake Photo";
	magic        = [/^Apple QuickTake \d+ photo/, /^Apple QuickTake \d+ Raw Image/, /^Macintosh QuickDraw PICT.* with decompressor "kTake/];
	metaProvider = ["image"];
	converters   = ["dcraw", "pfsconvert", "iconvert"];
}

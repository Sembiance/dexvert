/*
import {Format} from "../../Format.js";

export class tiff extends Format
{
	name = "Tagged Image File Format";
	website = "http://fileformats.archiveteam.org/wiki/TIFF";
	ext = [".tif",".tiff"];
	mimeType = "image/tiff";
	magic = ["Tagged Image File Format","TIFF image data"];
	priority = 3;
	converters = [{"program":"deark","flags":{"dearkNoThumbs":true}},"convert","imageAlchemy","graphicWorkshopProfessional"]

inputMeta = undefined;
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name     : "Tagged Image File Format",
	website  : "http://fileformats.archiveteam.org/wiki/TIFF",
	ext      : [".tif", ".tiff"],
	mimeType : "image/tiff",
	magic    : ["Tagged Image File Format", "TIFF image data"],
	priority : C.PRIORITY.LOW	// Often other formats are mis-identified as TIFF files such RAW camera files like Sony ARW and kodak*
};

// Some TIFF files, have invalid properties (hi100.tiff) that causes imagemagick to produce a 'transparent' image, even though there is data in the image. Weird.
// We can get around it by removing the alpha channel: {program : "convert", flags : {removeAlpha : true}}
// But deark doesn't seem to have this issue so we'll stick with it as the first priority
exports.converterPriority = [{program : "deark", flags : {dearkNoThumbs : true}}, "convert", "imageAlchemy", "graphicWorkshopProfessional"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

*/

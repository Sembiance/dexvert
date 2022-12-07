import {Format} from "../../Format.js";

export class pcd extends Format
{
	name       = "Kodak Photo CD Picture";
	website    = "http://fileformats.archiveteam.org/wiki/Photo_CD";
	ext        = [".pcd"];
	mimeType   = "image/x-photo-cd";
	magic      = [/Kodak Photo CD [Ii]mage/, "Kodak PhotoCD bitmap", /^fmt\/211( |$)/];
	// Used to have a metaProvider from convert, but oh boy is it unreliable at determining the width x height: http://discmaster.textfiles.com/view/731/PCD1235.BIN/photo_cd/images/img0067.pcd
	converters = ["pcdtojpeg", "convert", `abydosconvert[format:${this.mimeType}]`, "nconvert", "hiJaakExpress", "picturePublisher", "corelPhotoPaint", "canvas", "tomsViewer", "corelDRAW", "pv[matchType:magic]"];

	// If it fails, it often produces a 2x2 or 1x1 image, so exclude those
	verify = ({meta}) => meta.width>2 && meta.height>2;
}

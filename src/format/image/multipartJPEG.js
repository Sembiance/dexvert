import {Format} from "../../Format.js";

export class multipartJPEG extends Format
{
	name       = "Multipart JPEG";
	magic      = ["MIME multipart JPEG (mpjpeg)"];
	converters = ["foremost[skipVerify]"];	// often has HUNDREDS of embedded images, so just skip verification
}

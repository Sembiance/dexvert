import {Format} from "../../Format.js";

export class base64EncodedImage extends Format
{
	name       = "Base64 Encoded Image";
	magic      = [/^MIME Base64 encoded (BMP|GIF|JPEG|PNG) bitmap/];
	converters = ["base64 -> convert"];
}

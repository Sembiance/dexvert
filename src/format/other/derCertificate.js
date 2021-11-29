import {Format} from "../../Format.js";

export class derCertificate extends Format
{
	name           = "DER Encoded Certificate";
	ext            = [".cer"];
	forbidExtMatch = true;
	magic          = ["DER encoded X509 Certificate", "Certificate, Version=3"];
	converters     = ["openssl[command:x509][encoding:der]"];
}

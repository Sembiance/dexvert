import {Format} from "../../Format.js";

export class derCertificate extends Format
{
	name           = "DER Encoded Certificate";
	website        = "http://fileformats.archiveteam.org/wiki/DER_encoded_certificate";
	ext            = [".cer", ".der", ".crt"];
	forbidExtMatch = true;
	magic          = ["DER encoded X509 Certificate", "Certificate, Version=3", "DER Encoded Key Pair", "Certificate in DER format", /^DER verschl.sseltes, bin.res X\.509 Zertifikat/];
	converters     = ["openssl[command:x509][encoding:der]"];
}

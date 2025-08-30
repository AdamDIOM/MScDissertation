<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="text" encoding="UTF-8" />
    <xsl:template match="/">
        <xsl:text>stop_id, stop_name, stop_lat, stop_lon&#10;</xsl:text>
        <xsl:for-each select="TransXChange/StopPoints/AnnotatedStopPointRef">
            <xsl:value-of select="StopPointRef"/><xsl:text>,"</xsl:text>
            <xsl:value-of select="CommonName"/><xsl:text>",</xsl:text>
            <xsl:choose>
                <xsl:when test="Location/Latitude">
                    <xsl:value-of select="Location/Latitude"/><xsl:text>,</xsl:text>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:text>E*</xsl:text><xsl:value-of select="Location/Easting"/><xsl:text>E*,</xsl:text>
                </xsl:otherwise>
            </xsl:choose>
            <xsl:choose>
                <xsl:when test="Location/Longitude">
                    <xsl:value-of select="Location/Longitude"/><xsl:text>&#10;</xsl:text>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:text>N*</xsl:text><xsl:value-of select="Location/Northing"/><xsl:text>N*&#10;</xsl:text>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:for-each>
    </xsl:template>
</xsl:stylesheet>
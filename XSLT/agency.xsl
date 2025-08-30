<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="text" encoding="UTF-8" />
    <xsl:template match="/">
        <xsl:text>agency_id, agency_name, agency_url, agency_timezone&#10;</xsl:text>
        <xsl:for-each select="TransXChange/Operators/Operator">
                <xsl:value-of select="OperatorCode"/><xsl:text>,</xsl:text>
                <xsl:value-of select="OperatorShortName"/><xsl:text>,</xsl:text>
                <xsl:text>https://bus.im,</xsl:text>
                <xsl:text>GMT&#10;</xsl:text>
        </xsl:for-each>
    </xsl:template>
</xsl:stylesheet>
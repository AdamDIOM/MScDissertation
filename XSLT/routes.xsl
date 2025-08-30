<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="text" encoding="UTF-8" />
    <xsl:template match="/">
        <xsl:text>route_id, agency_id, route_short_name, route_long_name, route_type&#10;</xsl:text>
        <xsl:for-each select="TransXChange/Services/Service">
            <xsl:variable name="op" select="RegisteredOperatorRef"/>
            <xsl:variable name="sc" select="ServiceCode"/>
            <xsl:for-each select="StandardService/JourneyPattern">
                <xsl:value-of select="$sc"/><xsl:text>-</xsl:text><xsl:value-of select="RouteRef"/><xsl:text>,</xsl:text>
                <xsl:for-each select="../../../../Operators/Operator">
                    <xsl:if test="./@id = $op">
                        <xsl:value-of select="OperatorCode"/>
                    </xsl:if>
                </xsl:for-each>
                <xsl:text>,</xsl:text>
                <xsl:value-of select="$sc"/><xsl:text>,</xsl:text>
                <xsl:if test="Direction = 'outbound'">
                    <xsl:value-of select="../Destination"/>
                </xsl:if>
                <xsl:if test="Direction = 'inbound'">
                    <xsl:value-of select="../Origin"/>
                </xsl:if><xsl:text>,</xsl:text>
                <xsl:text>3&#10;</xsl:text>
            </xsl:for-each>
        </xsl:for-each>
    </xsl:template>
</xsl:stylesheet>
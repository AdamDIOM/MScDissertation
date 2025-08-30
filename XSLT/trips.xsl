<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="text" encoding="UTF-8" />
    <xsl:template match="/">
        <xsl:text>trip_id, route_id, service_id&#10;</xsl:text>
        <xsl:for-each select="TransXChange/VehicleJourneys/VehicleJourney">
            <xsl:variable name="vjc" select="VehicleJourneyCode"/>
            <xsl:value-of select="ServiceRef"/><xsl:text>-</xsl:text><xsl:value-of select="VehicleJourneyCode"/><xsl:text>,</xsl:text>
            <xsl:variable name="jpref" select="JourneyPatternRef"/>
            <xsl:value-of select="ServiceRef"/><xsl:text>-</xsl:text>
            <xsl:for-each select="../../Services/Service/StandardService/JourneyPattern">
                <xsl:if test="./@id = $jpref">
                    <xsl:value-of select="RouteRef"/>
                </xsl:if>
            </xsl:for-each><xsl:text>,</xsl:text>
            <xsl:value-of select="ServiceRef"/><xsl:text>-</xsl:text><xsl:value-of select="$vjc"/><xsl:text>&#10;</xsl:text>
        </xsl:for-each>
    </xsl:template>
</xsl:stylesheet>
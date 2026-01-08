/**
 * D3 Bar Chart for Backlog Aging KPI
 * Uses proper data join pattern to prevent SVG stacking
 */
import { useEffect, useRef } from "react";
import * as d3 from "d3";
import type { BucketInfo } from "../api/types";

interface BacklogAgingChartProps {
  data: BucketInfo[];
  onBucketClick: (bucket: string) => void;
}

export default function BacklogAgingChart({
  data,
  onBucketClick,
}: BacklogAgingChartProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || !data || data.length === 0) return;

    // Chart dimensions
    const margin = { top: 20, right: 30, bottom: 60, left: 60 };
    const width = 600 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    // Clear existing content to prevent stacking
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    // Create main group
    const g = svg
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Scales
    const x = d3
      .scaleBand()
      .domain(data.map((d) => d.label))
      .range([0, width])
      .padding(0.2);

    const y = d3
      .scaleLinear()
      .domain([0, d3.max(data, (d) => d.count) || 0])
      .nice()
      .range([height, 0]);

    // X axis
    g.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(x))
      .selectAll("text")
      .attr("transform", "rotate(-45)")
      .style("text-anchor", "end");

    // Y axis
    g.append("g").call(d3.axisLeft(y).ticks(5));

    // Y axis label
    g.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 0 - margin.left)
      .attr("x", 0 - height / 2)
      .attr("dy", "1em")
      .style("text-anchor", "middle")
      .style("font-size", "14px")
      .text("Number of Tickets");

    // Bars with data join pattern
    const bars = g.selectAll(".bar").data(data);

    // Enter selection
    bars
      .enter()
      .append("rect")
      .attr("class", "bar")
      .attr("x", (d) => x(d.label) || 0)
      .attr("y", (d) => y(d.count))
      .attr("width", x.bandwidth())
      .attr("height", (d) => height - y(d.count))
      .attr("fill", "#4F46E5")
      .attr("cursor", "pointer")
      .on("mouseover", function () {
        d3.select(this).attr("fill", "#6366F1");
      })
      .on("mouseout", function () {
        d3.select(this).attr("fill", "#4F46E5");
      })
      .on("click", (event, d) => {
        onBucketClick(d.label);
      });

    // Add count labels on top of bars
    g.selectAll(".label")
      .data(data)
      .enter()
      .append("text")
      .attr("class", "label")
      .attr("x", (d) => (x(d.label) || 0) + x.bandwidth() / 2)
      .attr("y", (d) => y(d.count) - 5)
      .attr("text-anchor", "middle")
      .style("font-size", "12px")
      .style("font-weight", "bold")
      .text((d) => d.count);

    // Cleanup function to remove elements when component unmounts
    return () => {
      svg.selectAll("*").remove();
    };
  }, [data, onBucketClick]);

  return (
    <div className="chart-container">
      <h2 style={{ marginBottom: "20px", fontSize: "20px", fontWeight: "bold" }}>
        Backlog Aging
      </h2>
      <svg
        ref={svgRef}
        width={600}
        height={400}
        style={{ border: "1px solid #e5e7eb", borderRadius: "8px" }}
      />
    </div>
  );
}

import Bubble from "./Bubble";
import * as d3 from "d3"
import Layout from "./Layout";
import Trajectory from "./Trajectory";

class HistogramLayout extends Layout {
  extractor: <T extends Bubble>(b: T) => number
  route: <T extends Bubble>(b: T) => Trajectory
  yFloor: number
  scale: d3.ScaleLinear<number, number>
  radius: number
  range_min: number
  range_max: number
  domain_min: number
  domain_max: number
  range: number
  diameter: number
  domain: number
  nBuckets: number
  countLength: number
  bucketCounts: Array<number>
  bucketZero: number
  smoothing: boolean


  constructor(extractor: <T extends Bubble> (b: T) => number,
              route: <T extends Bubble>(b: T) => Trajectory,
              yFloor: number, scale: d3.ScaleLinear<number, number>, radius: number,
              duration: number = 3000,
              smoothing: boolean = false) {
    super()
    this.extractor = extractor
    this.route = route
    this.yFloor = yFloor
    this.scale = scale
    this.radius = radius

    this.range_min = scale.range()[0]
    this.range_max = scale.range()[1]
    this.range = this.range_max - this.range_min

    this.domain_min = scale.domain()[0]
    this.domain_max = scale.domain()[1]
    this.domain = this.domain_max - this.domain_min


    this.diameter = 2 * this.radius
    this.nBuckets = Math.floor(this.range / this.diameter)
    this.countLength = this.nBuckets * 11
    // console.log(`rn ${this.range_min} ${this.range_max}  dom:  ${this.domain_min} ${this.domain_max}:  ${this.countLength}`)
    this.bucketCounts = Array<number>(this.countLength).fill(0)
    this.bucketZero = this.nBuckets * 5
    this.duration = duration
    this.smoothing = smoothing
  }

  reset = () => {
    this.bucketCounts = Array<number>(this.countLength).fill(0)
  }


  setTargetLocation: (b: Bubble) => void = (b: Bubble) => {
    let d = this.extractor(b)
    let bucketX = Math.round((d - this.domain_min) / this.domain * this.nBuckets)
    let bucketIndex = bucketX + this.bucketZero

    let yPos = 0
    if (bucketIndex >= 0 && bucketIndex < this.countLength) {
      let n = this.bucketCounts[bucketIndex]
      this.bucketCounts[bucketIndex] = n + 1
      yPos = n
    }
    b.tx = this.diameter * bucketX
    b.ty = this.yFloor - (yPos * this.diameter + this.radius)
  }
}

export default HistogramLayout
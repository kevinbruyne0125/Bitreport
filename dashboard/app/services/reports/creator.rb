# frozen_string_literal: true

module Reports
  class Creator < Service
    validates :pair, :timeframe, :indicators, presence: true

    before_execute :add_default_indicators

    def initialize(pair:, timeframe:, indicators:)
      @pair = pair
      @timeframe = timeframe
      @indicators = indicators
    end

    private

    attr_reader :pair, :timeframe, :indicators

    def run
      Report.create!(pair: pair,
                     timeframe: timeframe,
                     indicators: indicators,
                     comment: comment,
                     image: image)
    end

    def add_default_indicators
      @indicators = (%w[price volume] + indicators).uniq.compact
    end

    def chart_data
      @chart_data ||= Reports::DataPreparer.new(pair: pair,
                                                timeframe: timeframe).call
    end

    def comment
      @comment ||= Reports::CommentGenerator.new(data: chart_data,
                                                 indicators: indicators).call + working_hard_text
    end

    def working_hard_text
      "\n\nWe're working hard on the comments section. Stay tuned for future updates!"
    end

    def plot
      @plot ||= Reports::ChartGenerator.new(data: chart_data,
                                            indicators: indicators).call
    end

    def image
      @image ||= Reports::OverlayGenerator.new(pair: pair,
                                               plot: plot,
                                               fill_date: chart_data['last'],
                                               timeframe: timeframe,
                                               comment: comment).call
    end
  end
end

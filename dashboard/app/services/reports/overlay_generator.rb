# frozen_string_literal: true

require 'image_processing/vips'

module Reports
  class OverlayGenerator < Service
    validates :pair, :fill_date, :timeframe, :comment, presence: true

    def initialize(pair:, plot:, fill_date:, timeframe:, comment:)
      @pair = pair
      @plot = Vips::Image.new_from_buffer(plot, '', access: :sequential)
      @fill_date = fill_date
      @timeframe = timeframe
      @comment = comment
    end

    private

    attr_reader :pair, :plot, :fill_date, :timeframe, :comment

    def run
      image = Tempfile.new(%w[plot .png], encoding: 'ascii-8bit')
      image.write(generate)
      image
    end

    def generate
      image = Vips::Image.new_from_file(background, access: :sequential).insert(@plot, 0, 110)
      image = timestamp.ifthenelse([54, 54, 49], symbol.ifthenelse([238], image, blend: true), blend: true)
      image = description.ifthenelse([54, 54, 49], image, blend: true)
      image = version.ifthenelse([54, 54, 49], image, blend: true)
      image.write_to_buffer('.png')
    end

    def background
      @background ||= Rails.root.join('app', 'assets', 'images', 'template.png').to_s
    end

    def symbol
      symbol = Vips::Image.text("#{pair.symbol} #{timeframe}h", font: 'PT Sans Bold 56', align: :centre)
      symbol.embed(820 - symbol.width / 2, 80 - symbol.height, 2048, 1024)
    end

    def timestamp
      timestamp = Vips::Image.text(Time.at(fill_date).strftime('%Y-%m-%d %H:%M UTC'), font: 'PT Sans Bold 32', align: :centre)
      timestamp.embed(1810 - timestamp.width / 2, 200 - timestamp.height, 2048, 1024)
    end

    def description
      description = TextLayerGenerator.new(x_offset: 1610, y_offset: 200)
      description.add_header('Comment')
      description.add_text(comment.strip)
      description.image
    end

    def version
      version = TextLayerGenerator.new(x_offset: 1995, y_offset: 0, font_size: 19)
      version.add_text("v#{Settings.version}", float: :right)
      version.image
    end
  end
end
